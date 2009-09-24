class CreateTasks < ActiveRecord::Migration
  def self.up
    create_table :tasks do |t|
      t.integer :priority
      t.string :command
      t.integer :status
      t.references :job

      t.timestamps
    end
  end

  def self.down
    drop_table :tasks
  end
end
